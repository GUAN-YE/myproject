using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;
using System.Web.UI;
using System.Web.UI.WebControls;
using System.Data.SqlClient;
using System.Data;


public partial class houtai : System.Web.UI.Page
{
    protected void Page_Load(object sender, EventArgs e)
    {
        if (!IsPostBack)
        {
            dbind();
        }
    }
        
         public void dbind()
    {
        SqlConnection qq = new SqlConnection("server=.;database=keti;uid=liubin;pwd=123");
        qq.Open();
        SqlDataAdapter ww = new SqlDataAdapter("select * from tupian1", qq);
        DataTable ee = new DataTable();
        ww.Fill(ee);
        this.GridView1.DataSource = ee;
        this.GridView1.DataKeyNames = new string[] { "tupian" };
        this.GridView1.DataBind();
        qq.Close();
    
    }
         protected void GridView1_RowCancelingEdit(object sender, GridViewCancelEditEventArgs e)
         {
             this.GridView1.EditIndex = -1;
             dbind();
         }
         protected void GridView1_RowEditing(object sender, GridViewEditEventArgs e)
         {
             this.GridView1.EditIndex = e.NewEditIndex;
             dbind();
         }
         protected void GridView1_RowDeleting(object sender, GridViewDeleteEventArgs e)
         {

             string aa = GridView1.DataKeys[e.RowIndex].Value.ToString();
             SqlConnection qq = new SqlConnection("server=.;database=keti;uid=liubin;pwd=123");
             qq.Open();
             SqlCommand cmd = new SqlCommand();
             cmd.CommandType = CommandType.Text;
             cmd.CommandText = "delete from tupian1 where tupian='"+aa+"'" ;
             cmd.Connection = qq;
             cmd.ExecuteNonQuery();
             cmd.Dispose();
             qq.Close();
             GridView1.EditIndex = -1;
             this.GridView1.DataBind();
             dbind();
         }
         protected void GridView1_RowUpdating(object sender, GridViewUpdateEventArgs e)
         {
             string aa = GridView1.DataKeys[e.RowIndex].Value.ToString();
             string ss = ((TextBox)(this.GridView1.Rows[e.RowIndex].Cells[1].Controls[0])).Text;
             string dd = ((TextBox)(this.GridView1.Rows[e.RowIndex].Cells[2].Controls[0])).Text;
             string ff = ((TextBox)(this.GridView1.Rows[e.RowIndex].Cells[3].Controls[0])).Text;
             string gg = ((TextBox)(this.GridView1.Rows[e.RowIndex].Cells[4].Controls[0])).Text;
             SqlConnection qq = new SqlConnection("server=.;database=keti;uid=liubin;pwd=123");
             qq.Open();
             SqlCommand cmd = new SqlCommand();
             cmd.CommandText = "update tupian1 set jiage='" + ss + "',xiangqing='" + ff + "',xinghao='" + dd + "',kucun='"+gg+"'where tupian='" + aa + "'";
             cmd.Connection = qq;
             cmd.ExecuteNonQuery();
             cmd.Dispose();
             qq.Close();
             GridView1.EditIndex = -1;
             this.GridView1.DataBind();
             dbind();
         }
         protected void Button1_Click(object sender, EventArgs e)
         {
             Server.Transfer("xinpin.aspx");
         }
         protected void Button2_Click(object sender, EventArgs e)
         {
             Server.Transfer("shouye.aspx");
         }


         protected void GridView1_RowDataBound(object sender, GridViewRowEventArgs e)
         {
             if (e.Row.RowType == DataControlRowType.DataRow)
             {
                 string str = e.Row.Cells[3].Text;
                 if (e.Row.Cells[3].Text.Length > 8)
                 {
                     e.Row.Cells[3].Text = str.Substring(0, 8) + "......";
                     e.Row.Cells[3].ToolTip = str;
                 }
             }
         }
}
    

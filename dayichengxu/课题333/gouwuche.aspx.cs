using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;
using System.Web.UI;
using System.Web.UI.WebControls;
using System.Data.SqlClient;
using System.Data;

public partial class gouwuche : System.Web.UI.Page
{
    protected void Page_Load(object sender, EventArgs e)
    {
        //this.Label1.Text = "欢迎" + Session["aa"] + "登录";
        if (!IsPostBack)
        {
            dbind();
            lb();
             
        }
    }
    public void dbind()
    {
        //读取购物车数据
        SqlConnection conn = new SqlConnection("server=.;database=keti;uid=liubin;pwd=123;");
        conn.Open();
        SqlDataAdapter da = new SqlDataAdapter("select * from gouwuche", conn);
        DataTable dt = new DataTable();
        da.Fill(dt);
        this.GridView1.DataSource = dt;
        this.GridView1.DataKeyNames = new string[] { "jiage" };
        this.GridView1.DataBind();
        conn.Close();

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
        cmd.CommandText = "delete from gouwuche where jiage='" + aa + "'";
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
        string dd = ((TextBox)(this.GridView1.Rows[e.RowIndex].Cells[0].Controls[0])).Text;
        string ff = ((TextBox)(this.GridView1.Rows[e.RowIndex].Cells[2].Controls[0])).Text;
        SqlConnection qq = new SqlConnection("server=.;database=keti;uid=liubin;pwd=123");
        qq.Open();
        SqlCommand cmd = new SqlCommand();
        cmd.CommandText = "update gouwuche set  shuliang='" + ff + "'where jiage='" + aa + "'";
        cmd.Connection = qq;
        cmd.ExecuteNonQuery();
        cmd.Dispose();
        qq.Close();
        GridView1.EditIndex = -1;
        this.GridView1.DataBind();
        dbind();
        //qq.Open();
        //SqlDataAdapter da = new SqlDataAdapter("select SUM(xioaji) as 总价 from [gouwuche] ", qq);
        //DataTable dt = new DataTable();
        //da.Fill(dt);
        //this.GridView2.DataSource = dt;
        //this.GridView2.DataBind();
        //qq.Close();
    }
    protected void Button1_Click(object sender, EventArgs e)
    {
        //Server.Transfer("fahuo.aspx");
    }
    public void lb()
    {
        SqlConnection qq = new SqlConnection("server=.;database=keti;uid=liubin;pwd=123");
        qq.Open();
        SqlDataAdapter da = new SqlDataAdapter("select SUM(xioaji) as 总价 from [gouwuche] ", qq);
        DataTable dt = new DataTable();
        da.Fill(dt);
        this.GridView2.DataSource = dt;
        this.GridView2.DataBind();
        qq.Close();
    }
    protected void Button1_Click1(object sender, EventArgs e)
    {
        //SqlConnection ll = new SqlConnection("server=.;database=keti;uid=liubin;pwd=123");
        //ll.Open();
        //SqlDataAdapter conn = new SqlDataAdapter("select count(*) from gouwuche", ll);
        //DataTable dw = new DataTable();
        //conn.Fill(dw);
        //string shuliang = dw.Rows[0][0].ToString();
        //int count = Convert.ToInt32(shuliang);
        //for (int i = 1; i < count; i++)
        //{
        //    SqlCommand comm = new SqlCommand("update tupian1  set xiaoliang +='" + (Convert.ToInt32(dw.Rows[i-1][2].ToString()) + Convert.ToInt32(dw.Rows[i-1][2].ToString())).ToString() + "' where xinghao='" + dw.Rows[i-1][2] + "'", ll);
        //    comm.ExecuteNonQuery();
           
        
         Response.Write("<script>alert('购买成功！')</script>");
    }
}